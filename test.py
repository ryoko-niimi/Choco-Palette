from dotenv import load_dotenv
import os

# .envファイルを読み込む
load_dotenv()

#.envの中のGOOGLE_MAPS_API_KEYを取得して変数（例：API_KEY）に代入
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

print(API_KEY)  # ←テスト：正しく読めているか確認