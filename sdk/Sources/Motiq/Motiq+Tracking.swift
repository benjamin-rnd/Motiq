//
//  Motiq+Tracking.swift
//  Motiq
//
//  Created by Benjamin Arndt on 21.06.26.
//

import AnyCodable
import Foundation

extension Motiq {
    
    public func track(event_name: String, properties: [String: AnyCodable] = [:]) async {
        var app_id: String?
        
        if case .crossApp(let appId) = trackingMode {
            app_id = appId
        } else {
            app_id = nil
        }
        
        let event = await Event(
            name: event_name,
            user_id: getIDFV(),
            session_id: getCurrentSessionID(),
            app_id: app_id,
            timestamp: getCurrentTime(),
            properties: properties
        )
        
        await storeEventInQueue(event)
    }
    
    private func getCurrentTime() -> String {
        return Date().ISO8601Format()
    }
    
}
