# ExchangeMusic API Server

2016 HackU at KITの出し物のためのAPI Server．  

Made by pudding that is the member of the team "tuna-kan".

## Requirements

macOS Sierra 10.12, Hmebrew 1.0.7, pyenv, 1.0.2, pyenv-virtualenv 1.0.0でテスト．

* Python 3.5.2
* click==6.6
* Flask==0.11.1
* Flask-SQLAlchemy==2.1
* itsdangerous==0.24
* Jinja2==2.8
* MarkupSafe==0.23
* PyMySQL==0.7.9
* requests==2.11.1
* SQLAlchemy==1.1.1
* Werkzeug==0.11.11

## Usage

### APIサーバの起動
`api.py`を実行．


### APIサーバへのリクエスト例

長期運用およびセキュリティを考えていないのでコードは無駄だらけ．あまり変なリクエストはやめたほうが良い．  
楽曲へのURL付加はひとまず後回し．  

#### ユーザー作成

* method: POST
* URL: /create_user
* data: 
```json
{
  "name": "ユーザ名",
  "passwd": "パスワード"
}
```

400が返ってきたらユーザ名が重複してる．

#### ユーザの情報を取得

本来はここに認証をかける．

* method: GET
* URL: /user/<user_id>
* response:
```json
{
  "exchange": null,  # すれ違い無し（ユーザ作成時）ではnull
  "id": 2, # ユーザID
  "name": "test1",  # 設定したユーザ名
  "playlists": [
    {
      "clips": [
        {
          "album": "D'AZUR", 
          "artist": "藍井エイル", 
          "title": "幻影"
        }, 
        {
          "album": "D'AZUR", 
          "artist": "藍井エイル", 
          "title": "ずっとそばで"
        },
        # 曲が最大で10曲ならぶ．  
        # playlistは月ごとに増える．
        {
          "album": "『ソードアート・オンラインII』OP_IGNITE", 
          "artist": "藍井エイル", 
          "title": "IGNITE (TV size ver.)"
        }
      ], 
      "month": 10, 
      "year": 2016
    }
  ]
}
```

#### すれ違いで交換したIDを元にプレイリスト取得

先ほどのメソッドでの`exchange`からサーバー側ですれ違ったユーザの最新のプレイリストを取得して返す．

* method: GET
* URL: /user/<exchange>/playlist
* response:
```json
{
  "clips": [
    {
      "album": "only my railgun", 
      "artist": "fripSide", 
      "title": "onlr my railgun"
    }, 
    {
      "album": "LEVEL5 -judgelight-", 
      "artist": "fripSide", 
      "title": "LEVEL5 -judgelight-"
    }, 
    # 曲が最大で10曲並ぶ
    {
      "album": "LEVEL3", 
      "artist": "Perfume", 
      "title": "ふりかえるといるよ"
    }
  ], 
  "month": 10, 
  "year": 2016
}
```

ユーザー名を含めるか迷い中．

#### プレイリストの更新

自分のプレイリストをサーバーへ投げる．サーバー側で時刻判断をする．

* method: POST
* URL: /user/<user_id/playlist
* data:
```json
[
    {
      "album": "D'AZUR", 
      "artist": "藍井エイル", 
      "title": "ツナガルオモイ"
    }, 
    {
      "album": "D'AZUR", 
      "artist": "藍井エイル", 
      "title": "青の世界"
    }, 
    {
      "album": "D'AZUR", 
      "artist": "藍井エイル", 
      "title": "BREAK OUT!"
    }
]
```

前回よりも少ない曲数で投げると，サーバ上のプレイリストの曲も少なくなる（面倒だったのでこの更新が入った時点で一度サーバ側更新対象をdelしてる）．

## License
MIT