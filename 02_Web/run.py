from server import app

if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(debug=True, port=3000, host='localhost')
