//
//  Motiq+Batching.swift
//  Motiq
//
//  Created by Benjamin Arndt on 21.06.26.
//

// get queue from Motiq+Queue.swift, put batch together and pass to Motiq+API.swift

extension Motiq {
    
    func buildBatch() async {
        guard !queue.isEmpty else { return }
        let batch = EventBatch(events: queue)
        clearQueue()
        
        isFlushTimerRunning = false
        flushTask?.cancel()
        
        print(batch)
        // send batch to Motiq+API.swift
    }
    
}
