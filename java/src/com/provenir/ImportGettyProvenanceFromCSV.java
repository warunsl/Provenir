package com.provenir;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;

import com.mongodb.BasicDBList;
import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBObject;
import com.mongodb.Mongo;

public class ImportGettyProvenanceFromCSV {

	public static void main(String[] args) {

		ImportGettyProvenanceFromCSV obj = new ImportGettyProvenanceFromCSV();
		obj.run();

	}

	public void run() {

		String csvFile = "ALL-NGA-FROM-GETTY-For-provenance.tsv";
		BufferedReader br = null;
		String line = "";
		String cvsSplitBy = "\t";
		Mongo mongoClient = null;
		mongoClient = MongoConnection.getConnection();
		DB db = mongoClient.getDB("548db");
		DBCollection coll = db.getCollection("provenanceGetty");
		int count = 0;

		try {

			br = new BufferedReader(new FileReader(csvFile));
			br.readLine();
			while ((line = br.readLine()) != null) {
				if (++count % 100 == 0) {
					System.out.println(count);
				}
				try {

					// use comma as separator
					String[] record = line.split(cvsSplitBy);
					String startDate = record[0];
					String endDate = record[1];
					String id = record[2];
					String title = record[5];
					String accession = record[7];
					String format = record[8];
					String provenance = "";
					for (int i = 9; i < record.length; i++) {
						if (!"".equals(record[i].trim())) {
							provenance += " | " + record[i];
						}
					}
					DBObject dbo = (BasicDBObject)coll.findOne(new BasicDBObject("accession",accession));
					if(dbo==null){
						dbo = new BasicDBObject();
						dbo.put("picId", Integer.parseInt(id));
						dbo.put("title", title);
						dbo.put("accession", accession);
						dbo.put("format", format);
						ArrayList<BasicDBObject> arr = new ArrayList<BasicDBObject>();
						BasicDBObject provenanceRecord = new BasicDBObject();
						provenanceRecord.put("provenance", provenance);
						provenanceRecord.put("startDate", startDate);
						provenanceRecord.put("endDate", endDate);
						arr.add(provenanceRecord);
						dbo.put("provenanceArr", arr);
						coll.insert(dbo);
					}else{
						BasicDBList arrList= (BasicDBList)dbo.get("provenanceArr");
						BasicDBObject provenanceRecord = new BasicDBObject();
						provenanceRecord.put("provenance", provenance);
						provenanceRecord.put("startDate", startDate);
						provenanceRecord.put("endDate", endDate);
						arrList.add(provenanceRecord);
						coll.save(dbo);
					}

				} catch (Exception e) {
					e.printStackTrace();
				}

				// break;
			}

		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			if (br != null) {
				try {
					br.close();
					mongoClient.close();
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		}

		System.out.println("Done");
	}
}