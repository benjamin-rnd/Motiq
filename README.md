# Motiq

Motiq is a self-hosted and privacy-friendly analytics SDK for iOS. It is a lightweight alternative to tools like Google Analytics.

Its main goal is to help you, as an app developer, better understand your users and figure out how they use your app.

Motiq is designed to collect only anonymized data, so your users won't encounter annoying tracking pop-ups.


## Features

- Customize event names and additional information you'd like to collect
- Offline queuing
- Automatic tracking of the user's sessions
- Track more than one app with a single server instance (works only if the apps are from the same developer)


## Installation

Motiq consists of two components that need to be set up separately: the Swift SDK for your iOS app, and the self-hosted server that receives and stores the analytics data.

### Swift-SDK
**Requirements:** iOS 16+, Swift 6

The installation process on the SDK side is relatively simple. Just add it to your Xcode project via SPM:
1. In Xcode, go to **File** -> **Add Package Dependencies**
2. Enter the repository URL `https://github.com/benjamin-rnd/Motiq`
3. Select a version rule (e.g. **Up to Next Major**) and click **Add Package**

Then configure the SDK in your `App` entry point:

```Swift
import Motiq

@main
struct MyApp: App {
  init() {
    Motiq.shared.configure(baseURL: "https://api.your-server.com", apiSecret: "yourApiSecret",
                           batchSize: 4, flushIntervalSeconds: 40, debugMode: false)
  }

  var body: some Scene {
    WindowGroup {
      ContentView()
    }
  }
}
```
### Server
The *server* is a FastAPI application and a SQLite database.

1. Clone the repository and install dependencies:
```bash
git clone https://github.com/benjamin-rnd/Motiq
cd Motiq
python -m venv .venv && source .venv/bin/activate
pip install -r api/requirements.txt
```
2. Start the server:
```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

> [!TIP]
> I recommended to run uvicorn as a `systemd` service behind a reverse proxy like Caddy or nginx.

> Detailed setup instructions, including reverse proxy configuration, will be 
> available in the server documentation soon.


## Usage

After configuration, you can track custom events anywhere in your app:

```swift
Motiq.shared.track("button_tapped", properties: ["button": "sign_up"])
```

Event names and properties are fully customizable - use any name and key-value pairs 
that make sense for your app.

Events are queued locally and sent to your server in batches, so they are not lost 
if the user is offline.


## Roadmap

- [ ] Web dashboard for analyzing collected data
- [ ] Migration from SQLite to proper database (e.g. PostgreSQL)
- [ ] Docker container for simplified server-side setup


## Contributing

This project is currently in early development. If you find a bug or have a feature request, feel free to open an issue - feedback is welcome!
    
