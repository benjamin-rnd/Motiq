//
//  Motiq+API.swift
//  Motiq
//
//  Created by Benjamin Arndt on 21.06.26.
//

import Foundation

extension Motiq {
    
    func sendBatchToAPI(_ batch: EventBatch) async throws {
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
        
        do {
            let (_, response) = try await URLSession.shared.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else { return }
            
            switch httpResponse.statusCode {
            case 201:
                break
            case 400...499:
                throw MotiqSendError.clientError(httpResponse.statusCode)
            case 500...599:
                throw MotiqSendError.serverError(httpResponse.statusCode)
            default:
                throw MotiqSendError.serverError(0)
            }
        } catch _ as URLError {
            throw MotiqSendError.networkUnavailable
        }
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

enum MotiqSendError: Error {
    
    case networkUnavailable
    case serverError(Int)
    case clientError(Int)
    
}
