//
//  Motiq+Persistence.swift
//  Motiq
//
//  Created by Benjamin Arndt on 09.07.26.
//

import Foundation

extension Motiq {
    
    private func writeQueueToStorage(_ events: [Event]) {
        let url = FileManager.default
            .urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("motiq_queue.json")
        
        do {
            let data = try JSONEncoder().encode(events)
            try data.write(to: url, options: .atomic)
        } catch {
            print("Error persisting queue: \(error)")
        }
    }
    
    func loadPersistedQueue() -> [Event] {
        let url = FileManager.default
            .urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("motiq_queue.json")
        
        do {
            let data = try Data(contentsOf: url)
            return try JSONDecoder().decode([Event].self, from: data)
        } catch {
            print("Error loading persisted queue: \(error)")
            return []
        }
    }
    
    func persistQueue() {
        var queueToPersist = loadPersistedQueue()
        queueToPersist.append(contentsOf: queue)
        
        writeQueueToStorage(queueToPersist)
    }
    
    func isPersistedQueueEmpty() -> Bool {
        loadPersistedQueue().isEmpty
    }
    
    func clearPersistedQueue() {
        try? FileManager.default.removeItem(at: FileManager.default
            .urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("motiq_queue.json"))
    }
    
}
