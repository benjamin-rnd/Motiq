//
//  Motiq+Tracking.swift
//  Motiq
//
//  Created by Benjamin Arndt on 21.06.26.
//

import AnyCodable
import Foundation

extension Motiq {
    
    public func track(event_name: String, properties: [String: Any] = [:]) async {
        var app_id: String?
        
        if case .crossApp(let appId) = trackingMode {
            app_id = appId
        } else {
            app_id = nil
        }
        
        let codableProperties = properties.mapValues { AnyCodable($0) }
        
        let event = await Event(
            name: event_name,
            user_id: getIDFV(),
            session_id: getCurrentSessionID(),
            app_id: app_id,
            timestamp: getCurrentTime(),
            properties: codableProperties
        )
        
        await storeEventInQueue(event)
    }
    
    private func getCurrentTime() -> String {
        return Date().ISO8601Format()
    }
    
    func trackAppLaunch() async {
        let properties: [String: Any] = await [
            "device_model": getDevice(),
            "os_version": getOSVersion(),
            "app_version": getAppVersion(),
            "color_scheme": getColorScheme(),
            "orientation": getOrientation(),
            "connectivity": getConnectivity(),
            "accessibility_features": getEnabledAccessibilityFeatures()
        ]
        
        await track(event_name: "app_launch", properties: properties)
    }
    
    func trackAppClose() async {
        await track(event_name: "app_close")
    }
    
}
