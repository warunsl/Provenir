package com.provenir;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Set;

import javax.activation.MimeType;

import org.apache.commons.io.FileUtils;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.openrdf.model.impl.URIImpl;
import org.openrdf.query.BindingSet;
import org.openrdf.query.TupleQuery;
import org.openrdf.query.TupleQueryResult;
import org.openrdf.repository.Repository;
import org.openrdf.repository.RepositoryConnection;
import org.openrdf.repository.http.HTTPRepository;

public class DbpediaGetProperties {

	private static Repository rep = null;

	public static void main(String[] args) throws Exception {
		rep = new HTTPRepository("http://dbpedia.org/sparql");
		JSONParser parser = new JSONParser();
		JSONObject urlsObj = (JSONObject)parser.parse(new FileReader("dbpediaForImg.json"));
		JSONArray arr  = (JSONArray)urlsObj.get("urls");
		Iterator<JSONObject> iterator = arr.iterator();
        while (iterator.hasNext()) {
            JSONObject obj = (JSONObject)iterator.next();
            System.out.println();
            List list = runSPARQL("SELECT ?obj WHERE {<"+obj.get("url")+"> dbpedia-owl:thumbnail ?obj}");
            if(list!=null && list.size()>0){
            	String imgURL = ((HashMap<String, URIImpl>) list.get(0)).get("obj")
            			.toString();
            	obj.put("imgURL", imgURL);  
            	System.out.println("");
            }
        }
        File file = new File("imgURLs.json");
		FileUtils.write(file,arr.toString(),"UTF-8");
		System.out.println("Done");

	}

	public static List runSPARQL(String qs) {
		try {
			RepositoryConnection con = rep.getConnection();
			try {
				TupleQuery query = con.prepareTupleQuery(
						org.openrdf.query.QueryLanguage.SPARQL, qs);
				TupleQueryResult qres = query.evaluate();
				ArrayList reslist = new ArrayList();
				while (qres.hasNext()) {
					BindingSet b = qres.next();
					Set names = b.getBindingNames();
					HashMap hm = new HashMap();
					for (Object n : names) {
						hm.put((String) n, b.getValue((String) n));
					}
					reslist.add(hm);
				}
				return reslist;
			} finally {
				con.close();
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
		return null;
	}
}
