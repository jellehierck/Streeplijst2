


def test_index(client, test_app):
    response = client.get('/streeplijst/')
    assert 'http://localhost/login' == response.headers['Location']

    response = client.get('/streeplijst/home')
    assert 'http://localhost/login' == response.headers['Location']

    response = client.get('/streeplijst/index')
    assert 'http://localhost/login' == response.headers['Location']