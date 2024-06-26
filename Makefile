start_backend:
	@echo "Starting dev backend..."
	cd backend && fastapi dev app/main.py

start_frontend:
	@echo "Starting dev frontend..."
	cd frontend && npm run dev

install_frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

build_frontend:
	@echo "Building frontend..."
	cd frontend && npm run build
