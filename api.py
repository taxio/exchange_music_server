from flask import Flask, request, abort, jsonify
import json
import hashlib
from datetime import datetime
from session import Session
import models


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


def create_user_response(user_data):
    return jsonify({
        "id": user_data.id,
        "name": user_data.name,
        "playlists": [
            create_playlist_response(playlist) for playlist in user_data.playlists
        ],
        "exchange": [ex.exchange_id for ex in user_data.exchange]
    })


def create_playlist_response(playlist):
    return {
        "year": playlist.year,
        "month": playlist.month,
        "clips": [
            create_clip_response(clip) for clip in playlist.clips
        ]
    }


def create_clip_response(clip):
    return {
        "title": clip.title,
        "album": clip.album,
        "artist": clip.artist
    }


@app.route('/users', methods=["GET"])
def return_user():
    j = {
        "users": [],
    }
    with Session() as sess:
        users = sess.query(models.User).all()
        for user in users:
            user_data = {
                "id": user.id,
                "name": user.name,
                "exchange": user.exchange.exchange_id
            }
            j["users"].append(user_data)
        return jsonify(j)


@app.route('/create_user', methods=["POST"])
def create_user():
    content_dict = json.loads(request.data.decode("utf-8"))
    with Session() as sess:
        try:
            user = models.User(name=content_dict["name"], passwd=["passwd"])
            user.exchange = models.Exchange(exchange_id=None)
            sess.add(user)
            sess.commit()
        except Exception:
            abort(400)
        current_user = sess.query(models.User).filter_by(name=content_dict["name"]).first()
        response = jsonify({
            "id": current_user.id,
            "name": current_user.name
        })
        response.status_code = 200
        return response


@app.route("/user/<user_id>", methods=["GET"])
def return_specific_user(user_id):
    with Session() as sess:
        user_data = sess.query(models.User).filter_by(id=user_id).first()
        if user_data:
            response = create_user_response(user_data)
            response.status_code = 200
            return response
        else:
            abort(404)


@app.route("/user/<user_id>/playlist", methods=["GET"])
def return_user_playlist(user_id):
    with Session() as sess:
        user_data = sess.query(models.User).filter_by(id=user_id).first()
        if user_data is None:
            abort(404)
        try:
            response = jsonify([create_playlist_response(user_data.playlists[i]) for i in range(len(user_data.playlists))])
            response.status_code = 200
            return response
        except IndexError:
            abort(404)


@app.route("/user/<user_id>/exchange", methods=["GET"])
def return_exchange_playlist(user_id):
    with Session() as sess:
        user_data = sess.query(models.User).filter_by(id=user_id).first()
        ex_ids = user_data.exchange
        if ex_ids is None:
            abort(404)
        if len(ex_ids) == 0:
            abort(404)
        exchange_playlists = []
        for ex_id in ex_ids:
            exchange_user = sess.query(models.User).filter_by(id=ex_id.exchange_id).first()
            if exchange_user:
                try:
                    exchange_playlists.append(create_playlist_response(exchange_user.playlists[0]))
                except IndexError:
                    pass
        if len(exchange_playlists) > 0:
            return jsonify(exchange_playlists)
        else:
            abort(404)


@app.route("/user/<user_id>/playlist", methods=["POST"])
def update_playlist(user_id):
    def insert_clips(clips, session, playlist=None):
        if playlist is None:
            playlist = models.PlayList(year=now.year, month=now.month)
            session.add(playlist)
        for clip in clips:
            clip_info = clip['title'] + clip["artist"] + clip["album"]
            clip_hash = hashlib.sha1(clip_info.encode("utf-8")).hexdigest()
            clip_in_db = sess.query(models.Clip).filter_by(unique_hash=clip_hash).first()
            if clip_in_db is None:
                new_clip = models.Clip(title=clip["title"], artist=clip["artist"], album=clip["album"])
                session.add(new_clip)
                playlist.clips.append(new_clip)
            else:
                playlist.clips.append(clip_in_db)
        return playlist
    now = datetime.now()
    new_playlist = json.loads(request.data.decode("utf-8"))
    if len(new_playlist) > 10:
        abort(400)
    with Session() as sess:
        user_data = sess.query(models.User).filter_by(id=user_id).first()
        for playlist in user_data.playlists:
            if playlist.year == now.year and playlist.month == now.month:
                del playlist.clips[:]
                insert_clips(new_playlist, sess)
                sess.commit()
        else:
            inserted_playlist = insert_clips(new_playlist, sess)
            user_data.playlists.append(inserted_playlist)
            sess.commit()
            response = jsonify(create_playlist_response(user_data.playlists[0]))
            response.status_code = 200
            return response

if __name__ == "__main__":
    app.run()




