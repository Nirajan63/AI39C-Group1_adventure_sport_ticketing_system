# Server Execution Entry Point
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Start the server on port 5000
    app.run(debug=False, port=5000)
