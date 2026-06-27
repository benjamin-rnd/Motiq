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
        await trackAppClose()
    }
    
    func handleAppLaunchFromBackground() async {
        sessionID = generateNewSessionID()
        await trackAppLaunch()
    }
    
    func handleAppTerminate() {
        print("App terminated")
        // TODO: Add offline queueing here --> will be added later
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
        
        NotificationCenter.default.addObserver(
            forName: UIApplication.willTerminateNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            Task { await self?.handleAppTerminate() }
        }
    }
    
}
