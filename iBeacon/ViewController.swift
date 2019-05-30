//
//  ViewController.swift
//  iBeacon
//
//  Created by ESD 07 on 2019/4/30.
//  Copyright © 2019年 0760230. All rights reserved.
//

import UIKit
import WebKit
import CoreLocation
extension Dictionary{
    func jsonString() -> String {
        
        
        //print("is json valid \(JSONSerialization.isValidJSONObject(self))" )
        
        if let data =  try? JSONSerialization.data(withJSONObject: self, options: [])
        {
            return String.init(data: data, encoding: .utf8) ?? "JSON decode error"
            
        }else
        {
            return "JSON decode error"
        }
        
    }
}

extension URLRequest{
    var prettyPrint:String {
        var message = "\n---REQUEST------------------\n```\n"
        message = message + "URL: \(self.url!)\n"
        message = message + "METHOD: \(self.httpMethod!)\n"
        for (header,headerValue) in self.allHTTPHeaderFields! {
            message = message + "\(header): \(headerValue)\n"
        }
        message = message + "BODY: \(String.init(data: self.httpBody!, encoding: .utf8)!)\n"
        message = message + "```\n----------------------------\n"
        
        return message
    }
}

extension URLResponse{
    var prettyPrint:String{
        var httpResponse = self as! HTTPURLResponse
        var message = "\n---RESPONSE------------------\n```\n"
        message = message + "Header: \(httpResponse.allHeaderFields)\n"
        message = message + "URL: \(httpResponse.url!)\n"
        message = message + "MIMEType: \(httpResponse.mimeType!)\n"
        message = message + "Status Code: \(httpResponse.statusCode)\n"
        message = message + "```\n----------------------------\n"
        
        return message
    }
}
class ViewController: UIViewController,CLLocationManagerDelegate{
    var locationManager: CLLocationManager = CLLocationManager()
    let uuid = "32B64064-B3E9-482F-9F94-488846BD958F"
    let identifier = "shaking region"
    var enablePost = false
    @IBOutlet weak var rangingResultTextView: UITextView!
    @IBOutlet weak var monitorResultTextView: UITextView!
    
    // web
    let url = URL(string: "http://140.113.144.98:6000/")!
    let path = "/ibeacon"
    var timer:Timer!
    //session
    let config = URLSessionConfiguration.default
    var session:URLSession!
    @IBOutlet weak var XTextField: UITextField!
    @IBOutlet weak var YTextField: UITextField!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        let region = CLBeaconRegion(proximityUUID: UUID.init(uuidString:
            uuid)!, identifier: identifier)
        locationManager.delegate = self
        //
        region.notifyEntryStateOnDisplay = true
        region.notifyOnEntry = true
        region.notifyOnExit = true
        //
        locationManager.startMonitoring(for: region)
        if CLLocationManager.isMonitoringAvailable(for: CLBeaconRegion.self){
            if CLLocationManager.authorizationStatus() !=
                CLAuthorizationStatus.authorizedAlways
            {
                locationManager.requestAlwaysAuthorization()
            }
            
        }
        // web
        config.requestCachePolicy = .reloadIgnoringLocalCacheData
        config.urlCache = nil
        session = URLSession.init(configuration: config)
    
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    func locationManager(_ manager: CLLocationManager, didStartMonitoringFor region:
        CLRegion) {
        monitorResultTextView.text = "did start monitoring \(region.identifier)\n" +
            monitorResultTextView.text
        
    }
    func locationManager(_ manager: CLLocationManager, didEnterRegion region:
        CLRegion) {
        monitorResultTextView.text = "did enter\n" + monitorResultTextView.text
        
    }
    func locationManager(_ manager: CLLocationManager, didExitRegion region: CLRegion)
    {
        monitorResultTextView.text = "did exit\n" + monitorResultTextView.text
        
    }
    func locationManager(_ manager: CLLocationManager, didDetermineState state:
        CLRegionState, for region: CLRegion) {
        switch state {
        case .inside:
            //
            monitorResultTextView.text = "state inside\n" + monitorResultTextView.text
            
            if CLLocationManager.isRangingAvailable(){
                manager.startRangingBeacons(in: region as! CLBeaconRegion)
            }
        case .outside:
            //
            monitorResultTextView.text = "state outside\n" + monitorResultTextView.text
            manager.stopMonitoring(for: region)

        default:
            break
        }
        
    }
    func locationManager(_ manager: CLLocationManager, didRangeBeacons beacons:
        [CLBeacon], in region: CLBeaconRegion) {
        //
        rangingResultTextView.text = ""
        
        let orderedBeaconArray = beacons.sorted(by: { (b1, b2) -> Bool in
            return b1.rssi > b2.rssi
        })
        //
        for beacon in beacons {
            //
            var proximityString = ""
            switch beacon.proximity {
            case .far:
                proximityString = "far"
            case .near:
                proximityString = "near"
            case .immediate:
                proximityString = "immediate"
            default :
                proximityString = "unknow"
            }
            //
            rangingResultTextView.text = rangingResultTextView.text +
                "Major: \(beacon.major)" + " Minor: \(beacon.minor)" +
                " RSSI: \(beacon.rssi)" + " Proximity: \(proximityString)" +
                " Accuracy: \(beacon.accuracy)" + "\n\n";
            if (enablePost){
                let task = postTrainingData(with: Date(), didRangeBeacon: beacon) {
                    print("Post complete")
                }
                print("send task: \(task)")
            }
        }
        
    }
    @IBAction func startPostDataButton(_ sender: UIButton) {
        enablePost = true
        XTextField.resignFirstResponder()
        YTextField.resignFirstResponder()
    }
    @IBAction func stopPostDataButton(_ sender: UIButton) {
        enablePost = false
        XTextField.resignFirstResponder()
        YTextField.resignFirstResponder()
    }
    


    func postTrainingData(with time:Date, didRangeBeacon beacon:
        CLBeacon, completionHandler: @escaping () -> () ) -> URLSessionDataTask {
        var x = -1, y = -1
        if let xi = Int(XTextField.text!), let yi = Int(YTextField.text!){
            x = xi
            y = yi
        }
        let dict:[String:Any] = [ "timestamp": ISO8601DateFormatter().string(from: time),
                                  "major":beacon.major,
                                  "minor":beacon.minor,
                                  "rssi":String(beacon.rssi),
                                  "x":x,
                                  "y":y
                                  ]
        
        let task = postJsonString(dict.jsonString(), toPath: path, completionHandler: completionHandler)
        
        return task
    }
    
    func postJsonString(_ jsonString:String, toPath path:String, completionHandler: @escaping () -> () ) -> URLSessionDataTask {
        
        //create url
        var components = URLComponents.init()
        components.scheme = "http"
        components.host = "140.113.144.98"
        components.port = 6000
        components.path = path
        
        //create request
        var request = URLRequest.init(url: components.url!)
        //cache policy
        request.cachePolicy = .reloadIgnoringLocalAndRemoteCacheData
        //request type
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        
        //create body
        let postData = jsonString.data(using: .utf8)
        request.httpBody = postData
        
        
        print(request.prettyPrint)
        
        let dataTask =  session.dataTask(with: request) { (data, response, error) in
            if error != nil
            {
                //error
            }else
            {
                print(response?.prettyPrint)
                guard let httpResponse = response as? HTTPURLResponse else{ return }
                if httpResponse.statusCode != 200  {
                    
                    //error
                    
                }else
                {
                    completionHandler()
                }
            }
        }
        
        dataTask.resume()
        
        return dataTask
        
    }
}

