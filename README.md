# AI Server Control

Web dashboard for monitoring AI inference servers (oMLX, llama.cpp, Ollama) with a clean, intuitive interface.

---

## ⚙️ Configuration

Edit `config.json`:

```json
{
  "servers": [
    {
      "name": "ollama-local",
      
      "type": "ollama",
      "base_url": "http://localhost:11434",
      "api_key": ""
    }
  ],
  "refresh_intervals": [2, 5, 10, 30, 60],
  "default_refresh": 10
}
```

### Server Types

| Type | Type Name | Description |
|------|-----------|-------------|
| `ollama` | Ollama | Ollama local/server |
| `llamacpp` | LLaMA.cpp | llama.cpp servers |
| `omlx` | oMLX | oMLX servers |

### Config Fields

- `name` - Server name (shown in subtitle)
- `type` - Adapter type (`ollama`, `llamacpp`, `omlx`)
- `type_name` - Type name displayed on dashboard (e.g., "Ollama", "LLaMA.cpp", "oMLX")
- `base_url` - Server endpoint URL
- `api_key` - API key (if required)
- `refresh_intervals` - Available refresh rate options (seconds)
- `default_refresh` - Default refresh rate

---

## 🚀 Getting Started

### Method 1: Manual

**1. Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Configure servers**

```bash
cp config.json.sample config.json
```

**4. Run server**

```bash
python server.py
```

Or with uvicorn directly:

```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

**5. Open dashboard**

Visit: **http://localhost:8000**

---

### Method 2: Docker

**1. Configure servers**

```bash
cp config.json.sample config.json
```

**2. Build & run**

```bash
docker build -t ai-monitor .
docker run -p 8000:8000 \
  -v $(pwd)/config.json:/app/config.json \
  ai-monitor
```

**3. Open dashboard**

Visit: **http://localhost:8000**

---

## 📡 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Web dashboard |
| `GET /api/status` | Get status of all servers |
| `GET /config` | Get public config info |

---

## 🏗️ Project Structure

```
ai-monitor/
├── server.py          # FastAPI backend
├── adapters/          # Server adapters
│   ├── base.py
│   ├── llamacpp.py
│   ├── ollama.py
│   └── omlx.py
├── config.json.sample # Sample config
├── templates/         # HTML templates
├── requirements.txt
└── Dockerfile
```

---

## 📝 License

GNU GPL-3.0

---

# AI Server Control

Dashboard theo dõi trạng thái các AI inference servers (oMLX, llama.cpp, Ollama) với giao diện web đẹp mắt.

---

## ⚙️ Cấu hình

Chỉnh sửa `config.json`:

```json
{
  "servers": [
    {
      "name": "ollama-local",
      
      "type": "ollama",
      "base_url": "http://localhost:11434",
      "api_key": ""
    }
  ],
  "refresh_intervals": [2, 5, 10, 30, 60],
  "default_refresh": 10
}
```

### Các loại Server

| Type | Tên Type | Mô tả |
|------|----------|-------|
| `ollama` | Ollama | Ollama local/server |
| `llamacpp` | LLaMA.cpp | llama.cpp servers |
| `omlx` | oMLX | oMLX servers |

### Các trường trong Config

- `name` - Tên server (hiển thị trong subtitle)
- `type` - Loại adapter (`ollama`, `llamacpp`, `omlx`)
- `type_name` - Tên type hiển thị trên dashboard (ví dụ: "Ollama", "LLaMA.cpp", "oMLX")
- `base_url` - URL endpoint của server
- `api_key` - API key (nếu cần)
- `refresh_intervals` - Các tùy chọn refresh rate (giây)
- `default_refresh` - Refresh rate mặc định

---

## 🚀 Cách chạy

### Cách 1: Thủ công

**1. Tạo virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

**2. Cài đặt dependencies**

```bash
pip install -r requirements.txt
```

**3. Cấu hình servers**

```bash
cp config.json.sample config.json
```

**4. Chạy server**

```bash
python server.py
```

Hoặc với uvicorn:

```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

**5. Mở dashboard**

Truy cập: **http://localhost:8000**

---

### Cách 2: Docker

**1. Cấu hình servers**

```bash
cp config.json.sample config.json
```

**2. Build & chạy**

```bash
docker build -t ai-monitor .
docker run -p 8000:8000 \
  -v $(pwd)/config.json:/app/config.json \
  ai-monitor
```

**3. Mở dashboard**

Truy cập: **http://localhost:8000**

---

## 📡 API Endpoints

| Endpoint | Mô tả |
|----------|-------|
| `GET /` | Dashboard web |
| `GET /api/status` | Lấy trạng thái tất cả servers |
| `GET /config` | Lấy thông tin config (public) |

---

## 🏗️ Cấu trúc Project

```
ai-monitor/
├── server.py          # FastAPI backend
├── adapters/          # Adapter cho từng loại server
│   ├── base.py
│   ├── llamacpp.py
│   ├── ollama.py
│   └── omlx.py
├── config.json.sample # Config mẫu
├── templates/         # HTML templates
├── requirements.txt
└── Dockerfile
```

---

## 📝 License

GNU GPL-3.0