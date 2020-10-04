from flask import redirect, url_for

from streeplijst2.routes import login_required


def test_hello(client):
    response = client.get("/hello")
    assert response.data == b"Hello, World!"


def test_login_required(client):
    response = client.get("/secret_hello")
    assert 'http://localhost/login' == response.headers['Location']