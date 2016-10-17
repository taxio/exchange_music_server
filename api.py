from flask import Flask, request, abort, jsonify
from sqlalchemy import and_
import json
from datetime import datetime
from session import Session
from models import User, Exchange, PlayList, Clip


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


def create_user_response(user_data):
    return jsonify({
        "id": user_data.id,
        "name": user_data.name,
        "playlists": [create_playlist_response(playlist) for playlist in user_data.playlists],
        "exchange": user_data.exchange.exchange_id
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
        users = sess.query(User).all()
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
            user = User(name=content_dict["name"], passwd=["passwd"])
            user.exchange = Exchange(exchange_id=None)
            sess.add(user)
            sess.commit()
        except Exception:
            abort(400)
        current_user = sess.query(User).filter_by(name=content_dict["name"]).first()
        response = jsonify({
            "id": current_user.id,
            "name": current_user.name
        })
        response.status_code = 200
        return response


@app.route("/user/<user_id>", methods=["GET"])
def return_specific_user(user_id):
    with Session() as sess:
        user_data = sess.query(User).filter_by(id=user_id).first()
        if user_data:
            response = create_user_response(user_data)
            response.status_code = 200
            return response
        else:
            abort(404)


@app.route("/user/<user_id>/playlist", methods=["GET"])
def return_user_playlist(user_id):
    with Session() as sess:
        user_data = sess.query(User).filter_by(id=user_id).first()
        if user_data is None:
            abort(404)
        try:
            p = create_playlist_response(user_data.playlists[0])
        except IndexError:
            abort(404)
        response = jsonify(p)
        response.status_code = 200
        return response


@app.route("/user/<user_id>/exchange", methods=["GET"])
def return_exchange_playlist(user_id):
    with Session() as sess:
        user_data = sess.query(User).filter_by(id=user_id).first()
        ex_id = user_data.exchange.exchange_id
        if ex_id:
            exchange_user = sess.query(User).filter_by(id=ex_id).first()
            if exchange_user is None:
                abort(404)
            try:
                exchange_playlist = exchange_user.playlists[0]
                response = jsonify(create_playlist_response(exchange_playlist))
                return response
            except IndexError:
                abort(404)


@app.route("/user/<user_id>/playlist", methods=["POST"])
def update_playlist(user_id):
    def incert_clips(clips, playlist, session):
        for clip in clips:
            clip_in_db = sess.query(Clip).filter(
                and_(
                    Clip.title == clip['title'],
                    Clip.album == clip["album"],
                    Clip.artist == clip["artist"]
                )
            ).first()
            if clip_in_db is None:
                new_clip = Clip(title=clip["title"], artist=clip["artist"], album=clip["album"])
                session.add(new_clip)
                playlist.clips.append(new_clip)
                session.commit()
            else:
                playlist.clips.append(clip_in_db)
                session.commit()
    now = datetime.now()
    new_playlist = json.loads(request.data.decode("utf-8"))
    if len(new_playlist) > 10:
        abort(400)
    with Session() as sess:
        user_data = sess.query(User).filter_by(id=user_id).first()
        for playlist in user_data.playlists:
            if playlist.year == now.year and playlist.month == now.month:
                del playlist.clips[:]
                incert_clips(new_playlist, playlist, sess)
        else:
            new_month_playlist = PlayList(year=now.year, month=now.month)
            sess.add(new_month_playlist)
            user_data.playlists.append(new_month_playlist)
            incert_clips(new_playlist, new_month_playlist, sess)
            response = jsonify(create_playlist_response(user_data.playlists[0]))
            response.status_code = 200
            return response

if __name__ == "__main__":
    app.run()