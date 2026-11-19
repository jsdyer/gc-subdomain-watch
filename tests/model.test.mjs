import test from 'node:test';
import assert from 'node:assert/strict';
import {compare,selection} from '../web/model.mjs';
test('Changed paths, removals, additions and stable links have separate meanings',()=>{
 const r=compare({One:'https://a.ca/a',Two:'https://b.ca',Four:'https://z.ca'},{One:'https://a.ca/b',Three:'https://c.ca',Four:'https://z.ca'});
 assert.deepEqual(r.map(x=>x.state),['Unchanged','Destination changed','Added','Removed']);
 assert.equal(selection(r,'Changes','a.ca/a').length,1);assert.equal(selection(r,'All','').length,4);
});
