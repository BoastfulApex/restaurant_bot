# 🍽 Aksu Restaurant — Telegram Mini App

## Loyiha strukturasi
```
restaurant_bot/
├── backend/          # Django + DRF
│   ├── config/       # Settings, URLs
│   ├── products/     # Mahsulotlar app
│   ├── orders/       # Buyurtmalar app
│   └── requirements.txt
├── bot/              # Telegram bot (aiogram)
│   └── main.py
├── frontend/         # React Mini App
│   └── src/App.js
└── .env.example
```

---

## O'rnatish

### 1. Backend (Django)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# .env fayl yarating
cp ../.env.example .env
# .env faylni to'ldiring

# Migrations
python manage.py makemigrations
python manage.py migrate

# Superuser (admin panel uchun)
python manage.py createsuperuser

# Ishga tushirish
python manage.py runserver
```

### 2. Bot
```bash
cd bot
# .env fayldagi TELEGRAM_BOT_TOKEN ni to'ldiring
python main.py
```

### 3. Frontend (React)
```bash
cd frontend
npm install

# .env fayl yarating
echo "REACT_APP_API_URL=http://localhost:8000/api" > .env

npm start        # Development
npm run build    # Production (build/ papkasi)
```

---

## Deploy qilish

### Backend (Nginx + Gunicorn)
```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Frontend
```bash
npm run build
# build/ papkasini Nginx orqali serve qiling
```

### Nginx config
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend (Mini App)
    location / {
        root /var/www/restaurant/frontend/build;
        try_files $uri /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    # Django Admin
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    # Media fayllar
    location /media/ {
        alias /var/www/restaurant/backend/media/;
    }
}
```

---

## Telegram Bot sozlash

1. @BotFather dan bot yarating: `/newbot`
2. Token ni `.env` ga qo'shing
3. Mini App URL ni sozlang: `/newapp` yoki `/setmenubutton`
4. `ADMIN_CHAT_ID` ni olish: @userinfobot ga `/start` yuboring

---

## Admin panel

`https://yourdomain.com/admin/` — Django Admin
- Mahsulot va kategoriya qo'shish
- Buyurtmalarni ko'rish va status o'zgartirish
- Yangi buyurtma kelganda Telegram orqali xabar keladi
