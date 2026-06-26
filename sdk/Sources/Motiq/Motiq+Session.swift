//
//  Motiq+Session.swift
//  Motiq
//
//  Created by Benjamin Arndt on 21.06.26.
//

/*
 MARK: ABLAUF:
 - bei App-Start wird configure() aufgerufen, also passiert Folgendes: SessionID generieren, observeAppLifecycle() registrieren, app_launched()
 - App ganz normal schließen bzw. in Hintergrund: app_closed
 - App aus Hintergrund wieder starten = "Mini-Neustart": neue SessionID & app_launched()
   --> kein vollständiger Neustart, daher wird configure() auch nicht neu aufgerufen
 - Start nach Force-Close = kompletter Neustart, also wird configure() neu aufgerufen --> siehe oben
 */

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
