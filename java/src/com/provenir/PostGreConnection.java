package com.provenir;

import java.sql.Connection;
import java.sql.DriverManager;

public class PostGreConnection {
	private static Connection connection = null;
	

	public static Connection getConnection() {
		if (connection == null) {
			try {
				Class.forName("org.postgresql.Driver");
//				connection = DriverManager
//						.getConnection(
//								"jdbc:postgresql://ec2-107-20-206-36.compute-1.amazonaws.com:5432/d9lt10fug2vpts",
//								"priqjyipaxalbk", "ExyyHwCppN_A2gsXRlAiDmS8jG");
				
				connection = DriverManager
						.getConnection(
								"jdbc:postgresql://127.0.0.1:5432/test",
								"postgres", "gladon");
				//connection.close();
			} catch (Exception e) {
				System.out
						.println("error in db connection : " + e.getMessage());
			}
		}
		return connection;
	}
}
