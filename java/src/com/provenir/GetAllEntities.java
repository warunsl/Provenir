package com.provenir;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;


public class GetAllEntities {

	public static void main(String[] args){
		Connection con = PostGreConnection.getConnection();
		try {
			Statement st = con.createStatement();
			ResultSet rs = st.executeQuery("select * from node where type = 'Company' OR type= 'Organization' OR type = 'Facility'");
			JSONArray arr = new JSONArray();
			while(rs.next()){
				String url = rs.getString(1);
				String label = rs.getString(2);
				String type = rs.getString(3);
				JSONObject obj = new JSONObject();
				try {
					obj.put("url", url);
					obj.put("label", label);
					obj.put("type", type);
				} catch (JSONException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
				arr.put(obj);	
				
			}
			File file = new File("entitiesToReconcile.json");
			FileWriter fw = new FileWriter(file.getAbsoluteFile());
			BufferedWriter bw = new BufferedWriter(fw);
			bw.write(arr.toString());
			bw.close();
			System.out.println("Done");
			
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}finally{
			try {
				con.close();
			} catch (SQLException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		
		
		
		//con.close();
		

		
	}
}
