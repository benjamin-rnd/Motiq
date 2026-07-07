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
            dump(batch)
            return
        }
        
        guard let payload = encodeBatchToJSON(batch) else {
            return
        }
        
        guard let apiEndpoint = baseURL?.appending(path: "/events/batch") else {
            print("Batch not sent due to error while accessing correct API endpoint.")
            return
        }

        var request = URLRequest(url: apiEndpoint)
        request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpMethod = "POST"
        request.httpBody = payload
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error {
                print("Error while sending batch to API: \(error)")
                return
            }
            
            /*guard let data else { return }
            
            if let json = try? JSONSerialization.jsonObject(with: data) {
                print("Response:", json)
            }*/
            
            guard let httpResponse = response as? HTTPURLResponse else { return }
            
            if httpResponse.statusCode != 201 {
                print("Unexpected status code: \(httpResponse.statusCode)")
            }
        }

        task.resume()
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
