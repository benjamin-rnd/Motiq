//
//  Motiq+Persistence.swift
//  Motiq
//
//  Created by Benjamin Arndt on 09.07.26.
//

import Foundation

extension Motiq {
    
    private func getQueueFileURL() -> URL {
        let directory = FileManager.default
            .urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("motiq_queue.json")
        
        try? FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        
        return directory.appendingPathComponent("motiq_queue.json")
    }
    
    private func writeQueueToStorage(_ events: [Event]) {
        do {
            let data = try JSONEncoder().encode(events)
            try data.write(to: getQueueFileURL(), options: .atomic)
        } catch {
            print("Error persisting queue: \(error)")
        }
    }
    
    func loadPersistedQueue() -> [Event] {
        // check if file motiq_queue.json exists, otherwise an error is thrown
        let url = getQueueFileURL()
        
        guard FileManager.default.fileExists(atPath: url.path) else {
            return []
        }
        
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
        try? FileManager.default.removeItem(at: getQueueFileURL())
    }
    
}
