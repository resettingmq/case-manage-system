# 1. 插入纪录时设置settled_amount

DROP TRIGGER IF EXISTS payable_before_insert;

DELIMITER //
CREATE TRIGGER payable_before_insert BEFORE INSERT
  ON purchase_payable
  FOR EACH ROW
BEGIN
  SET NEW.unsettled_amount = NEW.amount;
END //
DELIMITER ;


# 1. 在更新记录时根据amount的变化量修改unsettled_amount
# 2. 档enabled从1变为0时，
#     2.1 更新所有关联receipts.enabled为0(注意在receipts update的时候不要触发receivable的update)
#       这一约束该为在model删除时进行验证， 如果存在enabled的子receipts，则不能被disabled

DROP TRIGGER IF EXISTS payable_before_update;

DELIMITER //
CREATE TRIGGER payable_before_update BEFORE UPDATE
  ON purchase_payable
  FOR EACH ROW
BEGIN
  SET @amount_delta = NEW.amount - OLD.amount;
  IF @amount_delta != 0 THEN
    -- 需要判断@amount_delta,
    -- 避免直接update unsettled_amount时不会更新unsettled_amount的bug
    SET NEW.unsettled_amount = OLD.unsettled_amount + @amount_delta;
  END IF;
END//
DELIMITER ;