package org.example;

public class Main {
    public static void main(String[] args) throws Exception {

       if (args.length < 3) {
           System.out.println("Please provide a repository URL, output file path and default branch as arguments.");
           System.exit(1);
       }
       String repoUrl = args[0];
       String outputFilePath = args[1];
       String defaultBranch = args[2];
//        bndtools/bndtools
        //voldemort/voldemort
        //apache/maven
//         String repoUrl = "https://github.com/dustin/java-memcached-client.git";
//        String repoUrl = "https://github.com/mongodb/mongo-java-driver.git";
//         String outputFilePath = "M:\\Data\\Dal\\Term2\\ML\\Lab\\test_2.jsonl";
//         String defaultBranch = "master";


        ExtractVariableExtractor extractMethodExtractor = new ExtractVariableExtractor(repoUrl,defaultBranch);
        extractMethodExtractor.identifyRefactoringInstances().generateSamples(outputFilePath);

    }
}