package com.provenir;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class PostgreDBHelper {

	Connection connection = null;
	PreparedStatement psEdge = null;
	PreparedStatement psNode = null;
	
	public PostgreDBHelper() {
		connection = PostGreConnection.getConnection();
		try {
			psEdge = connection.prepareStatement("INSERT INTO edge VALUES(?,?,?)");
			psNode = connection.prepareStatement("INSERT INTO node VALUES(?,?,?)");
		} catch (SQLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	public void saveEdge(String source, String target, String label){
		try {
			psEdge.setString(1,source);
			psEdge.setString(2,target);
			psEdge.setString(3,label);
			psEdge.executeUpdate();
		} catch (SQLException e) {
			// TODO Auto-generated catch block
			//System.out.println(e.getMessage());
		}
	}
	
	public void saveNode(String id, String label, String type){
		try {
			psNode.setString(1,id);
			psNode.setString(2,label);
			psNode.setString(3,type);
			psNode.executeUpdate();
		} catch (SQLException e) {
			// TODO Auto-generated catch block
			//System.out.println(e.getMessage());
		}
	}
}
