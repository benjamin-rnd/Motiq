//
//  Models.swift
//  Motiq
//
//  Created by Benjamin Arndt on 21.06.26.
//

import AnyCodable

struct Event: Codable {
    let name: String
    let user_id: String
    let session_id: String
    let app_id: String?
    let timestamp: String
    let properties: [String: AnyCodable]
    
    enum CodingKeys: String, CodingKey {
        case name = "event_name"
        case user_id
        case session_id
        case app_id
        case timestamp
        case properties
    }
}

struct EventBatch: Codable {
    let events: [Event]
}
