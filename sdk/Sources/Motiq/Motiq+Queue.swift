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
            guard !Task.isCancelled else { return }
            flushQueue()
        }
    }
    
    func cancelFlushTimer() {
        isFlushTimerRunning = false
        flushTask?.cancel()
    }
    
    func flushQueue() {
        guard !queue.isEmpty else { return }
        guard !isFlushing else { return }
        isFlushing = true
        
        cancelFlushTimer()
        let batch = buildBatch()
        
        Task {
            defer { isFlushing = false }
            do {
                try await sendBatchToAPI(batch)
                clearQueue()
                flushPersistedQueue()
            } catch let error as MotiqSendError {
                switch error {
                case .networkUnavailable:
                    print("Batch send failed with network error, will persist batch")
                    persistQueue()
                    clearQueue()
                case .serverError(let statusCode):
                    print("Batch send failed due to server error with status code: \(statusCode)")
                    persistQueue()
                    clearQueue()
                case .clientError(let statusCode):
                    print("Batch send failed due to client error with status code: \(statusCode)")
                    clearQueue()
                }
            }
        }
    }
    
    func flushPersistedQueue() {
        guard !isPersistedQueueEmpty() else { return }
        queue.append(contentsOf: loadPersistedQueue())
        clearPersistedQueue()
        flushQueue()
    }
    
}
