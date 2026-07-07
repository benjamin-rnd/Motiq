//
//  Motiq+API.swift
//  Motiq
//
//  Created by Benjamin Arndt on 21.06.26.
//

import Foundation

extension Motiq {
    
    func sendBatchToAPI(_ batch: EventBatch) {
        guard debugMode == false else {
            print("Debug mode enabled, batch not sent to API. Batch payload:")
            print(batch)
            return
        }
        
        guard let payload = encodeBatchToJSON(batch) else {
            return
        }
        
        // TODO: send batch to API --> will be added later
    }
    
    private func encodeBatchToJSON(_ batch: EventBatch) -> Data? {
        do {
            let payload = try JSONEncoder().encode(batch)
            return payload
        } catch {
            print("Batch not sent due to encoding error: \(error)")
            return nil
        }
    }
    
}
