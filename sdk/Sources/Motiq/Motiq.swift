//
//  Motiq.swift
//  Motiq
//
//  Created by Benjamin Arndt on 21.06.26.
//

import Foundation

/// The Motiq analytics SDK for iOS.
///
/// Use ``shared`` to access the singleton instance. Call ``configure(baseURL:apiKey:trackingMode:batchSize:flushIntervalSeconds:debugMode:)``
/// once at app launch, then track events anywhere in your app with ``track(_:properties:)``.
///
/// ## Quick Start
/// ```swift
/// Motiq.shared.configure(baseURL: "https://analytics.example.com", apiKey: "your-api-key")
/// Motiq.shared.track("button_tapped", properties: ["screen": "home", "variant": "A"])
/// ```
public actor Motiq {
    
    /// The shared Motiq instance. Use this to access all SDK functionality.
    public static let shared = Motiq()
    
    /// Controls whether the SDK actively tracks and flushes events.
    /// Set to `false` to pause all tracking — no events will be queued or sent to the
    /// backend until re-enabled. Useful for suppressing analytics during testing.
    ///
    /// Defaults to `true`.
    ///
    /// ## Example
    /// ```swift
    /// // Disable
    /// Motiq.shared.isEnabled = false
    ///
    /// // Re-enable later
    /// Motiq.shared.isEnabled = true
    /// ```
    public var isEnabled: Bool = true
    
    var queue: [Event] = []
    var sessionID: String = ""
    var isFlushTimerRunning: Bool = false
    var flushTask: Task<Void, Never>?
    
    var cachedIDFV: String = ""
    var cachedOSVersion: String = ""
    var cachedOrientation: String = ""
    var cachedEnabledAccessibilityFeatures: [String] = []
    
    var baseURL: URL?
    var apiKey: String = ""
    var trackingMode: TrackingMode = .singleApp
    var batchSize: Int = 10
    var flushIntervalSeconds: Int = 45
    var debugMode: Bool = true

    private init() {}
    
    /// Configures the Motiq SDK with the given settings.
    ///
    /// Call this once at app launch (in your app entry point), before tracking any events.
    /// Wraps async initialization internally - no `await` needed.
    ///
    /// - Parameters:
    ///   - baseURL: The base URL of your self-hosted Motiq backend (e.g. `"https://analytics.example.com"`).
    ///   - apiKey: The API key used to authenticate requests against your Motiq backend.
    ///     Sent as the `X-API-Key` HTTP header on every request.
    ///   - trackingMode: Controls whether events are attributed to a single app or shared
    ///     across multiple apps on the same Motiq instance. Defaults to `.singleApp`.
    ///     Pass `.crossApp(appId:)` with a stable identifier (e.g. your Bundle ID) to enable
    ///     cross-app analytics. The `appId` is only included in event payloads when this mode is active.
    ///   - batchSize: The maximum number of events collected before a flush is triggered.
    ///     Defaults to `10`. Lower values reduce data loss on crash; higher values reduce network overhead.
    ///   - flushIntervalSeconds: How often (in seconds) the SDK automatically flushes
    ///     queued events to the backend, regardless of batch size. Defaults to `60`.
    ///   - debugMode: When `true`, the SDK prints detailed logs to the console and outputs
    ///     event batches via `dump()` instead of sending them to the backend. Useful during
    ///     development to inspect payloads without polluting your analytics data. Disable in production.
    ///
    /// - Note: To disable Motiq entirely at runtime (e.g. for testing), set ``isEnabled`` to `false`.
    ///
    /// - Important: Must be called before any call to ``track(_:properties:)``.
    ///   Calling `track` before `configure` will result in events being silently dropped.
    ///
    /// ## Example
    /// ```swift
    /// // your @main App struct
    /// Motiq.shared.configure(
    ///     baseURL: "https://analytics.example.com",
    ///     apiKey: "your-api-key",
    ///     trackingMode: .crossApp(appId: "com.example.MyApp"),
    ///     batchSize: 20,
    ///     flushIntervalSeconds: 60,
    ///     debugMode: false
    /// )
    ///  ```
    public nonisolated func configure(baseURL: String, apiKey: String, trackingMode: TrackingMode = .singleApp, batchSize: Int = 10, flushIntervalSeconds: Int = 60, debugMode: Bool) {
        Task {
            await internalConfigure(baseURL: baseURL, apiKey: apiKey, trackingMode: trackingMode, batchSize: batchSize, flushIntervalSeconds: flushIntervalSeconds, debugMode: debugMode)
        }
    }
    
    func internalConfigure(baseURL: String, apiKey: String, trackingMode: TrackingMode, batchSize: Int, flushIntervalSeconds: Int, debugMode: Bool) async {
        self.baseURL = baseURL.hasSuffix("/") ? URL(string: String(baseURL.dropLast())) : URL(string: baseURL)
        self.apiKey = apiKey
        self.trackingMode = trackingMode
        self.batchSize = batchSize
        self.flushIntervalSeconds = flushIntervalSeconds
        self.debugMode = debugMode
        
        sessionID = generateNewSessionID()
        self.cachedIDFV = await getIDFV()
        self.cachedOSVersion = await getOSVersion()
        self.cachedOrientation = await getOrientation()
        self.cachedEnabledAccessibilityFeatures = await getEnabledAccessibilityFeatures()
        trackAppLaunch()
        setupAppLifecycleObservers()
    }
    
    /// Controls whether events are attributed to a single app or across multiple apps
    /// on the same Motiq instance.
    public enum TrackingMode: Sendable {
        
        /// Tracks events for this app only. This is the default.
        case singleApp
        
        /// Tracks events across multiple apps sharing the same Motiq backend.
        /// The provided `appId` (e.g. your Bundle ID) is included in every event payload
        /// and stored in the database, allowing cross-app analysis.
        ///
        /// - Parameter appId: A stable identifier for this app, typically the Bundle ID.
        case crossApp(appId: String)
    }
    
}
