//
//  Motiq.swift
//  Motiq
//
//  Created by Benjamin Arndt on 21.06.26.
//

import Foundation

actor Motiq {
    
    public static let shared = Motiq()
    
    var queue: [Event] = []
    var isFlushTimerRunning: Bool = false
    var flushTask: Task<Void, Never>?
    
    var sessionID: String = ""
    
    var apiEndpoint: URL?
    var apiKey: String = ""
    var trackingMode: TrackingMode = .singleApp
    var batchSize: Int = 0
    var flushIntervalSeconds: Int = 0
    var debugMode: Bool = false

    private init() {}

    public func configure(apiEndpoint: String, apiKey: String, trackingMode: TrackingMode = .singleApp, batchSize: Int = 10, flushIntervalSeconds: Int = 45, debugMode: Bool = false) {
        Task {
            self.apiEndpoint = URL(string: apiEndpoint)
            self.apiKey = apiKey
            self.trackingMode = trackingMode
            self.batchSize = batchSize
            self.flushIntervalSeconds = flushIntervalSeconds
            self.debugMode = debugMode
            
            sessionID = generateNewSessionID()
            await trackAppLaunch()
            setupAppLifecycleObservers()
        }
    }

    enum TrackingMode {
        case singleApp
        case crossApp(appId: String)
    }
    
}
