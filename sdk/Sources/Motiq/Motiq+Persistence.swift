//
//  Motiq+Persistence.swift
//  Motiq
//
//  Created by Benjamin Arndt on 09.07.26.
//

import Foundation

extension Motiq {
    
    private func persistQueue(_ events: [Event]) {
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
    
    private func loadPersistedQueue() -> [Event] {
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
    
    func mergeWithPersistedQueue() {
        var queueToPersist = loadPersistedQueue()
        queueToPersist.append(contentsOf: queue)
        
        persistQueue(queueToPersist)
    }
    
}
