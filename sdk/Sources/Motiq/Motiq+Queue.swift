//
//  Motiq+Queue.swift
//  Motiq
//
//  Created by Benjamin Arndt on 21.06.26.
//

extension Motiq {
    
    func storeEventInQueue(_ event: Event) {
        queue.append(event)
        
        if !isFlushTimerRunning {
            startFlushTimer()
        }
        
        if isQueueAtBatchSize() {
            flushQueue()
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
            flushQueue()
        }
    }
    
    private func flushQueue() {
        guard !queue.isEmpty else { return }
        let batch = buildBatch()
        
        isFlushTimerRunning = false
        flushTask?.cancel()
        
        sendBatchToAPI(batch)
        clearQueue()
    }
    
}
