//
//  Motiq+Tracking.swift
//  Motiq
//
//  Created by Benjamin Arndt on 21.06.26.
//

import AnyCodable
import Foundation

extension Motiq {
    
    public nonisolated func track(event_name: String, properties: [String: any Sendable] = [:]) {
    public nonisolated func track(_ name: String, properties: [String: any Sendable] = [:]) {
        Task {
            await internalTrack(name: name, properties: properties)
        }
    }
    
    func internalTrack(name: String, properties: [String: Any] = [:]) async {
        guard isEnabled else {
            print("Motiq is disabled, skipping tracking")
            return
        }
        
        var app_id: String?
        
        if case .crossApp(let appId) = trackingMode {
            app_id = appId
        } else {
            app_id = nil
        }
        
        let codableProperties = properties.mapValues { AnyCodable($0) }
        
        let event = Event(
            name: name,
            user_id: cachedIDFV,
            session_id: sessionID,
            app_id: app_id,
            timestamp: getCurrentTime(),
            properties: codableProperties
        )
        
        storeEventInQueue(event)
    }
    
    private func getCurrentTime() -> String {
        return Date().ISO8601Format()
    }
    
    func trackAppLaunch() {
        let properties: [String: any Sendable] = [
            "device_model": getDevice(),
            "os_version": cachedOSVersion,
            "app_version": getAppVersion(),
            "color_scheme": getColorScheme(),
            "orientation": cachedOrientation,
            "connectivity": getConnectivity(),
            "accessibility_features": cachedEnabledAccessibilityFeatures
        ]
        
        track("app_launched", properties: properties)
    }
    
    func trackAppClose() {
        track("app_closed")
    }
    
}
