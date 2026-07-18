//
//  Motiq+Session.swift
//  Motiq
//
//  Created by Benjamin Arndt on 21.06.26.
//

import Foundation
import UIKit

extension Motiq {
    
    func generateNewSessionID() -> String {
        UUID().uuidString
    }
    
    func handleAppBackground() async {
        await internalTrack(name: "app_closed", properties: [:])
        flushQueue()
    }
    
    func handleAppLaunchFromBackground() {
        sessionID = generateNewSessionID()
        trackAppLaunch()
    }
    
    func setupAppLifecycleObservers() {
        NotificationCenter.default.addObserver(
            forName: UIApplication.didEnterBackgroundNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            Task { await self?.handleAppBackground() }
        }
        
        NotificationCenter.default.addObserver(
            forName: UIApplication.willEnterForegroundNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            Task { await self?.handleAppLaunchFromBackground() }
        }
    }
    
}
