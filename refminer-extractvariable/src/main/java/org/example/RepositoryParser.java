package org.example;

import org.eclipse.jgit.lib.ObjectId;
import org.eclipse.jgit.lib.Repository;
import org.eclipse.jgit.revwalk.RevCommit;
import org.eclipse.jgit.revwalk.RevWalk;
import org.json.JSONObject;

import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

public class RepositoryParser {

    private final Repository repo;
    private String parentSHA;

    private String commitSHA;

    public RepositoryParser(Repository repo) {

        this.repo = repo;
        this.parentSHA = null;
    }


    public void getParentSHA(String commitSHA) {
        ObjectId commitId = ObjectId.fromString(commitSHA);

        try {
            RevWalk revWalk = new RevWalk(this.repo);
            RevCommit commit = revWalk.parseCommit(commitId);
            RevCommit parent = revWalk.parseCommit(commit.getParent(0).getId());
            this.parentSHA = parent.getName();
        }
        catch (Exception e) {
            System.out.println("Exception: " + e);
        }
    }


    private ContentResult getCodeBody(int index, String key, JSONObject refactoring) throws Exception {

        ExtractMethodContent emc = new ExtractMethodContent(this.repo.getDirectory().getParent());
        boolean isLeftSide = Objects.equals(key, "leftSide");
        if (isLeftSide) {
            emc.checkoutToCommit(this.parentSHA);
        }
        else {
            emc.checkoutToCommit(this.commitSHA);
        }


        String filePath = Paths.get(this.repo.getDirectory().getParent(),
                refactoring.getJSONArray("rightSide").getJSONObject(index).getString("filePath")).toString();


        return emc.extractMethodContent(
                filePath,
                refactoring.getJSONArray("rightSide").getJSONObject(index).getInt("startLine"),
                refactoring.getJSONArray("rightSide").getJSONObject(index).getInt("endLine")
        );
    }

    public Map<String, Object> getSamples(JSONObject refactoring, boolean getContext) throws Exception {

        Map<String, Object> samples = new HashMap<>();

        commitSHA = refactoring.getString("commitID");
        int lineNo = refactoring.getJSONArray("rightSide").getJSONObject(0).getInt("startLine");
        getParentSHA(commitSHA);

        ContentResult positiveSample = this.getCodeBody(0, "leftSide", refactoring);
        int srcIndex = 1;
        int dstIndex = 0;

        ContentResult srcAfterRefactoring = this.getCodeBody(dstIndex, "rightSide", refactoring);

        if (getContext) {
            if(positiveSample != null && srcAfterRefactoring != null) {
                samples.put("lineNo", lineNo);
                samples.put("Smelly Sample", positiveSample.getClassContent());
                samples.put("Refactored Sample", srcAfterRefactoring.getClassContent());
            }
        }
        else {
            if(positiveSample != null && srcAfterRefactoring != null) {
                samples.put("lineNo", lineNo);
                samples.put("Smelly Sample", positiveSample.getMethodContent());
                samples.put("Refactored Sample", srcAfterRefactoring.getMethodContent());
            }
        }

        return samples;
    }
}
