// swift-tools-version: 6.3
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "Motiq",
    products: [
        // Products define the executables and libraries a package produces, making them visible to other packages.
        .library(
            name: "Motiq",
            targets: ["Motiq"]
        ),
    ],
    dependencies: [
        .package(
                url: "https://github.com/Flight-School/AnyCodable",
                from: "0.6.0"
            ),
    ],
    targets: [
        // Targets are the basic building blocks of a package, defining a module or a test suite.
        // Targets can depend on other targets in this package and products from dependencies.
        .target(
            name: "Motiq",
            dependencies: [
                .product(name: "AnyCodable", package: "AnyCodable")
            ]
        ),
        .testTarget(
            name: "MotiqTests",
            dependencies: ["Motiq"]
        ),
    ],
    swiftLanguageModes: [.v6]
)
