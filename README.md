# Ahoum CRM - Facilitator Backend

A FastAPI-based backend system for managing facilitators, courses, students, and campaigns in the Ahoum CRM ecosystem.

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- [UV package manager](https://docs.astral.sh/uv/) installed

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd facilitatorBackend-ahoum-crm
   ```

2. **Install dependencies using UV**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   # Copy the example environment file (if available)
   cp .env.example .env
   
   # Edit the .env file with your configuration
   # Add your database URL, WhatsApp credentials, etc.
   ```

4. **Run database migrations (if applicable)**
   ```bash
   uv run python migrations/add_course_promotion_tables.py
   ```

5. **Start the development server**
   ```bash
   uv run main.py
   ```

The API will be available at `http://localhost:8000`

## 📋 Available Commands

### Development

- **Start the server**: `uv run main.py`
- **Install new packages**: `uv add package-name`
- **Install dev dependencies**: `uv add --dev package-name`
- **Run tests**: `uv run pytest` (if tests are available)
- **Populate dummy data**: `uv run populate_dummy_data.py`

### Database

- **Test database connection**: `uv run test_db_connection.py`
- **Run migrations**: `uv run python migrations/add_course_promotion_tables.py`

### WhatsApp Integration

- **Test WhatsApp integration**: `uv run test_whatsapp_integration.py`

### System Setup

- **Set up unified system**: `uv run setup_unified_system.py`

## 🏗️ Project Structure

```
facilitatorBackend-ahoum-crm/
├── main.py                    # FastAPI application entry point
├── config.py                  # Application configuration
├── pyproject.toml            # UV project configuration
├── uv.lock                   # UV lock file (auto-generated)
├── middleware/               # Custom middleware
│   ├── auth_required.py
│   ├── session_required.py
│   └── subdomain_middleware.py
├── models/                   # Database models
│   ├── database.py
│   └── course_calling.py
├── routes/                   # API route handlers
│   ├── facilitator_routes.py
│   ├── courses_routes.py
│   ├── students_routes.py
│   ├── campaigns_routes.py
│   ├── offerings_routes.py
│   ├── phone_auth_routes.py
│   ├── website_routes.py
│   └── course_calling_routes.py
├── services/                 # Business logic services
│   └── whatsapp_service.py
├── migrations/               # Database migrations
│   └── add_course_promotion_tables.py
└── docs/                    # Documentation
    ├── API_ENDPOINTS.md
    ├── DEPLOYMENT_GUIDE.md
    ├── WHATSAPP_SETUP_GUIDE.md
    └── README_ECOSYSTEM.md
```

## 🔧 Configuration

The application uses environment variables for configuration. Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=your_database_url

# WhatsApp Integration
WHATSAPP_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

# Authentication
JWT_SECRET_KEY=your_secret_key

# Other configurations
DEBUG=true
PORT=8000
```

## 📚 API Documentation

Once the server is running, you can access:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

For detailed API endpoints, see [API_ENDPOINTS.md](API_ENDPOINTS.md)

## 🔌 Features

- **Facilitator Management**: CRUD operations for facilitators
- **Course Management**: Course creation, scheduling, and management
- **Student Management**: Student enrollment and tracking
- **Campaign Management**: Marketing campaign handling
- **WhatsApp Integration**: Automated messaging and notifications
- **Phone Authentication**: Secure phone-based authentication
- **Multi-tenant Support**: Subdomain-based multi-tenancy

## 🛠️ Development

### Adding New Dependencies

```bash
# Add a production dependency
uv add fastapi

# Add a development dependency
uv add --dev pytest

# Add a dependency with specific version
uv add "fastapi>=0.100.0"
```

### Database Operations

```bash
# Test database connection
uv run test_db_connection.py

# Populate with sample data
uv run populate_dummy_data.py
```

### Code Quality

```bash
# Format code (if formatter is installed)
uv run black .

# Lint code (if linter is installed)
uv run flake8 .

# Type checking (if mypy is installed)
uv run mypy .
```

## 🚀 Deployment

For production deployment, refer to [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## 🔗 WhatsApp Integration

For WhatsApp setup and configuration, see [WHATSAPP_SETUP_GUIDE.md](WHATSAPP_SETUP_GUIDE.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes
4. Commit your changes: `git commit -am 'Add new feature'`
5. Push to the branch: `git push origin feature/new-feature`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions, please refer to the documentation files or contact the development team.

## 📋 Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `config.py` or use `PORT` environment variable
2. **Database connection issues**: Verify your `DATABASE_URL` in the `.env` file
3. **WhatsApp integration fails**: Check your WhatsApp credentials and configuration

### UV Package Manager Issues

```bash
# Clear UV cache
uv cache clean

# Reinstall dependencies
rm uv.lock
uv sync

# Update all dependencies
uv sync --upgrade
```

For more detailed troubleshooting, see the individual documentation files in the `docs/` directory.
