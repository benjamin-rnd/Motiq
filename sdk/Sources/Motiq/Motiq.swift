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

    public enum TrackingMode: Sendable {
        case singleApp
        case crossApp(appId: String)
    }
    
}
