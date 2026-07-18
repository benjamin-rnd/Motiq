//
//  Motiq+Batching.swift
//  Motiq
//
//  Created by Benjamin Arndt on 21.06.26.
//

extension Motiq {
    
    func buildBatch() -> EventBatch {
        EventBatch(events: queue)
    }
    
}
