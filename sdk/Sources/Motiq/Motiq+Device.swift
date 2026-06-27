//
//  Motiq+Device.swift
//  Motiq
//
//  Created by Benjamin Arndt on 21.06.26.
//

import DeviceKit
import Foundation
import Network
import UIKit

extension Motiq {
    
    func getIDFV() async -> String {
        await UIDevice.current.identifierForVendor?.uuidString ?? "Unknown"
    }
    
    func getDevice() -> String {
        if debugMode && Device.current.isSimulator {
            print("Simulator detected: \(Device.current.safeDescription)")
        }
        
        if case .unknown = Device.current {
            return "Unknown"
        }
        return Device.current.safeDescription
    }
    
    func getAppVersion() -> String {
        Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "Unknown"
    }
    
    func getOSVersion() async -> String {
        await UIDevice.current.systemVersion
    }
    
    func getColorScheme() -> String {
        UITraitCollection.current.userInterfaceStyle == .dark ? "dark" : "light"
    }
    
    func getOrientation() async -> String {
        await MainActor.run {
            UIDevice.current.orientation.isLandscape ? "landscape" : "portrait"
        }
    }
    
    func getConnectivity() -> String {
        let monitor = NWPathMonitor()
        let path = monitor.currentPath
        
        if path.usesInterfaceType(.cellular) {
            return "cellular"
        } else if path.usesInterfaceType(.wifi) {
            return "wifi"
        } else if path.usesInterfaceType(.wiredEthernet) {
            return "ethernet"
        } else {
            return "Unknown"
        }
    }
    
    func getEnabledAccessibilityFeatures() async -> [String] {
        let enabledFeatures = await MainActor.run {
            var result: [String] = []
            
            if UIAccessibility.isBoldTextEnabled { result.append("bold_text") }
            if UIAccessibility.isDarkerSystemColorsEnabled { result.append("darker_system_colors") }
            if UIAccessibility.isReduceMotionEnabled { result.append("reduce_motion") }
            if UIAccessibility.isReduceTransparencyEnabled { result.append("reduce_transparency") }
            if UIAccessibility.isVoiceOverRunning { result.append("voice_over") }
            
            return result
        }
        
        return enabledFeatures
    }
    
}
