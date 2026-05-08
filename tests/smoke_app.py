from app import app


def main():
    client = app.test_client()

    for path in ['/api/check', '/api/settings', '/api/history?limit=1']:
        response = client.get(path)
        assert response.status_code == 200, (path, response.status_code, response.get_data(as_text=True))
        assert response.get_json() is not None

    response = client.post('/api/download', json={'url': ''})
    assert response.status_code == 400
    assert response.get_json()['error']

    response = client.get('/api/status/not-found')
    assert response.status_code == 404
    assert response.get_json()['error']

    print('smoke_app ok')


if __name__ == '__main__':
    main()
