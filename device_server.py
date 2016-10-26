import socketserver
import argparse
from session import Session
import models
import settings


# UDPサーバー割り込み処理
# デバッグ用ハンドラー
class DebugUDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip().decode('utf-8')
        user_list = data.split(",")
        device_user = user_list[0]
        passed_user = user_list[1:6]
        # これいるの？
        socket = self.request[1]
        print("device user ID:{}".format(device_user)) # デバイスの持ち主のID
        print("passed user ID:{}".format(passed_user)) # すれ違ったユーザーのID*5個


# データベース処理を含む本番用ハンドラー
class UDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip().decode('utf-8')
        user_list = data.split(",")
        device_user = user_list[0]
        passed_user = user_list[1:6]
        # これいるの？
        socket = self.request[1]
        self.update_exchange_ids(own_id=device_user, exchange_ids=passed_user)

    @staticmethod
    def update_exchange_ids(own_id, exchange_ids):
        try:
            if len(exchange_ids) < 6:
                with Session() as sess:
                    # ownerの情報を取得
                    owner = sess.query(models.User).filter_by(id=own_id).first()
                    current_exchanges = [owner.exchange[i].exchange_id for i in range(len(owner.exchange))]
                    ex_set = set(exchange_ids)
                    old_set = set(current_exchanges)
                    # 現在のownerが所持するidと送られてきたidで共通のもの
                    common_set = old_set & ex_set
                    # 現在の所持idになく，送られてきたidにはあるもの
                    new_set = ex_set - old_set
                    # 上記二つの和集合
                    actual_set = common_set | new_set
                    # Exchangeオブジェクトを生成
                    new_exchange = [models.Exchange(exchange_id=ex_id) for ex_id in list(actual_set)]
                    # データベースに追加
                    sess.add_all(new_exchange)
                    # 更新
                    owner.exchange = new_exchange
                    sess.commit()
        except Exception:
            # めんどいからエラー起こったらスルー
            pass


class DeviceServer:

    def __init__(self, debugging=True):
        # settings.pyでホストとポートを設定
        self.HOST = settings.SERVER_HOST
        self.PORT = settings.SERVER_PORT
        self.debugging = debugging

    def run(self):
        # サーバー立ち上げ
        # handlerを動的に決定．debugging=Trueならデバッグモード
        handler = DebugUDPHandler if self.debugging else UDPHandler
        server = socketserver.ThreadingUDPServer((self.HOST, self.PORT), handler)
        # 割り込みループ
        server.serve_forever()


def define_behavior():
    parser = argparse.ArgumentParser(
        description="This is the DeviceServer using UDP."
    )
    parser.add_argument("-a",
                        "--activate",
                        dest="activate",
                        default=False,
                        help="This option enable this script to update database.",
                        action="store_true"
                        )

    # コマンドラインで-aを指定しなかったときデバッグモード
    server = DeviceServer(debugging=False) if parser.parse_args().activate else DeviceServer()
    server.run()

if __name__ == "__main__":
    define_behavior()

