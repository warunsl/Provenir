package com.provenir;

import java.net.UnknownHostException;

import com.mongodb.Mongo;

public class MongoConnection {
	private static Mongo conn = null;
	
	public static Mongo getConnection(){
		if(conn!=null){
			return conn;
		}else{
			try {
				conn = new Mongo();
			} catch (UnknownHostException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			return conn;
		}
	}
	
	public static void closeConnection(){
		if(conn!=null){
			conn.close();
		}
	}
}
