//
//  Motiq+Queue.swift
//  Motiq
//
//  Created by Benjamin Arndt on 21.06.26.
//

// get event from Motiq+Tracking.swift, add it to queue and manage queue

extension Motiq {
    
    func storeEventInQueue(_ event: Event) async {
        queue.append(event)
        
        if !isFlushTimerRunning {
            startFlushTimer()
        }
        
        if isQueueAtBatchSize() {
            await buildBatch()
        }
    }
    
    private func isQueueAtBatchSize() -> Bool {
        queue.count >= batchSize
    }
    
    func clearQueue() {
        queue.removeAll()
    }
    
    private func startFlushTimer() {
        isFlushTimerRunning = true
        
        flushTask = Task {
            try? await Task.sleep(for: .seconds(flushIntervalSeconds))
            await buildBatch()
        }
    }
    
}
