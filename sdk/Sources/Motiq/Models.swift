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
}

struct EventBatch: Codable {
    let events: [Event]
}
