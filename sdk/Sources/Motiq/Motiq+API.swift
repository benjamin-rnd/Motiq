//
//  Motiq+API.swift
//  Motiq
//
//  Created by Benjamin Arndt on 21.06.26.
//

// get queue from Motiq+Queue.swift, encode it to JSON and pass to API (POST request)

import Foundation

extension Motiq {
    
    func encodeBatchToJSON(_ batch: EventBatch) {
        do {
            let payload = try JSONEncoder().encode(batch)
            sendBatch(payload)
        } catch {
            print("Batch not sent due to encoding error: \(error)")
        }
        
    }
    
    private func sendBatch(_ payload: Data) {
        guard debugMode == false else {
            if let jsonString = String(data: payload, encoding: .utf8) {
                print("Debug mode enabled, batch not sent to API. Batch payload:")
                print(jsonString)
            }
            return
        }
        
        // TODO: send batch to API --> will be added later
    }
    
}
