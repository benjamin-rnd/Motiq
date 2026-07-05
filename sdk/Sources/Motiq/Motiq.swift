//
//  Motiq.swift
//  Motiq
//
//  Created by Benjamin Arndt on 21.06.26.
//

import Foundation

public actor Motiq {
    
    public static let shared = Motiq()
    
    public var isEnabled: Bool = true
    
    var queue: [Event] = []
    var isFlushTimerRunning: Bool = false
    var flushTask: Task<Void, Never>?
    
    var sessionID: String = ""
    
    var cachedIDFV: String = ""
    var cachedOSVersion: String = ""
    var cachedOrientation: String = ""
    var cachedEnabledAccessibilityFeatures: [String] = []
    
    var apiEndpoint: URL?
    var apiKey: String = ""
    var trackingMode: TrackingMode = .singleApp
    var batchSize: Int = 10
    var flushIntervalSeconds: Int = 45
    var debugMode: Bool = true

    private init() {}

    public nonisolated func configure(apiEndpoint: String, apiKey: String, trackingMode: TrackingMode = .singleApp, batchSize: Int, flushIntervalSeconds: Int, debugMode: Bool) {
        Task {
            await internalConfigure(apiEndpoint: apiEndpoint, apiKey: apiKey, trackingMode: trackingMode, batchSize: batchSize, flushIntervalSeconds: flushIntervalSeconds, debugMode: debugMode)
        }
    }
    
    func internalConfigure(apiEndpoint: String, apiKey: String, trackingMode: TrackingMode, batchSize: Int, flushIntervalSeconds: Int, debugMode: Bool) async {
        self.apiEndpoint = URL(string: apiEndpoint)
        self.apiKey = apiKey
        self.trackingMode = trackingMode
        self.batchSize = batchSize
        self.flushIntervalSeconds = flushIntervalSeconds
        self.debugMode = debugMode
        
        sessionID = generateNewSessionID()
        self.cachedIDFV = await getIDFV()
        self.cachedOSVersion = await getOSVersion()
        self.cachedEnabledAccessibilityFeatures = await getEnabledAccessibilityFeatures()
        trackAppLaunch()
        setupAppLifecycleObservers()
    }

    public enum TrackingMode: Sendable {
        case singleApp
        case crossApp(appId: String)
    }
    
}
