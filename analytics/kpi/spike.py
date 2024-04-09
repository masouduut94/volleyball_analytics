from src.backend.app.api_interface import APIInterface


if __name__ == '__main__':
    api = APIInterface("http://localhost:8000")
    t = api.get_rallies(match_id=1)
    print(t[0])
