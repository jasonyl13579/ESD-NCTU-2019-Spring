//
//  InterfaceController.swift
//  ibeaconWatchDisplay Extension
//
//  Created by Huang Jason on 2019/5/17.
//  Copyright © 2019年 0760222. All rights reserved.
//

import WatchKit
import Foundation

class InterfaceController: WKInterfaceController {
    @IBOutlet weak var xlabel: WKInterfaceLabel!
    @IBOutlet weak var ylabel: WKInterfaceLabel!
    let url = URL(string: "http://140.113.144.98:6000/")!
    //let path = "/change_label"
    var timer:Timer!
    //session
    let config = URLSessionConfiguration.default
    var session:URLSession!
    override func awake(withContext context: Any?) {
        super.awake(withContext: context)
        
        
       
    }
    
    override func willActivate() {
        // This method is called when watch view controller is about to be visible to user
        super.willActivate()
    }
    
    override func didDeactivate() {
        // This method is called when watch view controller is no longer visible
        super.didDeactivate()
    }

    @IBAction func buttonPressed() {
        //self.xlabel.setText ("Server Fail")
        self.getTextFromServer()
    }
    func getTextFromServer() {
        URLSession.shared.dataTask(with: url, completionHandler: { (data, response, error) in
            if error != nil{
                print(error as Any)
                DispatchQueue.main.async {
                    self.xlabel.setText ("Server Fail")
                }
            }else{
                
                guard let data = data, error == nil else { return }
                print("Get Text Finished")
                print("\(data)")
                DispatchQueue.main.async() {
                    self.xlabel.setText(String(data: data, encoding: .utf8))
                }
                
            }
        }).resume()
    }
}
