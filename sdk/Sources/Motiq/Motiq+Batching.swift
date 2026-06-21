//
//  Motiq+Batching.swift
//  Motiq
//
//  Created by Benjamin Arndt on 21.06.26.
//

extension Motiq {
    
    func buildBatch() async {
        guard !queue.isEmpty else { return }
        let batch = EventBatch(events: queue)
        clearQueue()
        
        isFlushTimerRunning = false
        flushTask?.cancel()
        
        print(batch)
        // TODO: send batch to Motiq+API.swift
    }
    
}
